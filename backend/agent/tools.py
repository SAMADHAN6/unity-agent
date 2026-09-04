"""
Unity Agent Tools — custom tool functions the agent can call
"""

from langchain_core.tools import tool                            # fix: was langchain.tools
from knowledge.rag import search_unity_docs                      # absolute import (backend/ is cwd)


@tool
def search_docs(query: str) -> str:
    """
    Search the Unity knowledge base for documentation, guides, and tutorials.
    Use this for any Unity-specific question about APIs, features, or concepts.
    """
    results = search_unity_docs(query)
    if not results:
        return "No relevant documentation found. Answering from general Unity knowledge."
    return "\n\n".join(results)


@tool
def explain_error(error_message: str) -> str:
    """
    Explain a Unity console error or warning and suggest how to fix it.
    Input should be the exact error message from the Unity console.
    """
    context = search_unity_docs(error_message)
    context_text = "\n".join(context) if context else "No specific docs found."

    return (
        f"Analyzing Unity error: {error_message}\n\n"
        f"Related documentation context:\n{context_text}\n\n"
        "Common causes and fixes will be provided based on this error pattern."
    )


@tool
def generate_csharp_template(component_type: str) -> str:
    """
    Generate a C# Unity script template for a given component type.
    Examples: 'player controller', 'enemy AI', 'inventory system', 'singleton manager'
    """
    templates = {
        "singleton": '''\
using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
}''',
        "player controller": '''\
using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpHeight = 2f;
    [SerializeField] private float gravity = -9.81f;

    private CharacterController _controller;
    private Vector3 _velocity;

    private void Awake()
    {
        _controller = GetComponent<CharacterController>();
    }

    private void Update()
    {
        float x = Input.GetAxis("Horizontal");
        float z = Input.GetAxis("Vertical");

        Vector3 move = transform.right * x + transform.forward * z;
        _controller.Move(move * moveSpeed * Time.deltaTime);

        if (_controller.isGrounded && _velocity.y < 0)
            _velocity.y = -2f;

        if (Input.GetButtonDown("Jump") && _controller.isGrounded)
            _velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);

        _velocity.y += gravity * Time.deltaTime;
        _controller.Move(_velocity * Time.deltaTime);
    }
}''',
        "scriptable object": '''\
using UnityEngine;

[CreateAssetMenu(fileName = "NewData", menuName = "Game/Data")]
public class GameData : ScriptableObject
{
    [Header("Settings")]
    public string itemName;
    public int value;
    public Sprite icon;
    public string description;
}''',
        "enemy ai": '''\
using UnityEngine;
using UnityEngine.AI;

[RequireComponent(typeof(NavMeshAgent))]
public class EnemyAI : MonoBehaviour
{
    [Header("AI Settings")]
    [SerializeField] private Transform player;
    [SerializeField] private float detectionRange = 10f;
    [SerializeField] private float attackRange = 2f;

    private NavMeshAgent _agent;

    private void Awake()
    {
        _agent = GetComponent<NavMeshAgent>();
    }

    private void Update()
    {
        if (player == null) return;

        float distance = Vector3.Distance(transform.position, player.position);

        if (distance <= attackRange)
        {
            _agent.isStopped = true;
            Attack();
        }
        else if (distance <= detectionRange)
        {
            _agent.isStopped = false;
            _agent.SetDestination(player.position);
        }
        else
        {
            _agent.isStopped = true;
        }
    }

    private void Attack()
    {
        // TODO: implement attack logic
        Debug.Log("Enemy attacks!");
    }
}''',
        "object pool": '''\
using System.Collections.Generic;
using UnityEngine;

public class ObjectPool : MonoBehaviour
{
    [SerializeField] private GameObject prefab;
    [SerializeField] private int initialSize = 20;

    private readonly Queue<GameObject> _pool = new Queue<GameObject>();

    private void Awake()
    {
        for (int i = 0; i < initialSize; i++)
            _pool.Enqueue(CreateInstance());
    }

    private GameObject CreateInstance()
    {
        var obj = Instantiate(prefab, transform);
        obj.SetActive(false);
        return obj;
    }

    public GameObject Get(Vector3 position, Quaternion rotation)
    {
        var obj = _pool.Count > 0 ? _pool.Dequeue() : CreateInstance();
        obj.transform.SetPositionAndRotation(position, rotation);
        obj.SetActive(true);
        return obj;
    }

    public void Return(GameObject obj)
    {
        obj.SetActive(false);
        _pool.Enqueue(obj);
    }
}'''
    }

    lower_type = component_type.lower()
    for key, template in templates.items():
        if key in lower_type:
            return f"```csharp\n{template}\n```"

    return f"No pre-built template for '{component_type}'. The agent will generate a custom script."


def get_tools():
    """Return all available tools for the agent."""
    return [search_docs, explain_error, generate_csharp_template]
